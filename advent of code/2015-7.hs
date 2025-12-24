import Data.Bits
import qualified Data.Map.Lazy as Map

liness x = filter (not . null) $ lines x

consume :: Map.Map String Int -> String -> Int
consume m s = case reads s :: [(Int, String)] of 
                  [(val, "")] -> val
                  _           -> m Map.! s

interpret :: Map.Map String Int -> [String] -> Int
interpret m (x:y:z:_) | x == "NOT"    = (consume m y) .^. 65535
                    | y == "AND"    = a .&. b
                    | y == "OR"     = a .|. b
                    | y == "LSHIFT" = 65535 .&. shiftL a b
                    | y == "RSHIFT" = shiftR a b
                    | y == "->"     = a
                    | otherwise     = error "you dun fucked up"
                    where 
                      a = consume m x
                      b = consume m z

consumelines :: [String] -> Map.Map String Int -> Map.Map String Int
consumelines [] m = m
consumelines (x:xs) m = nm
                      where 
                        key = last ofwords
                        val = interpret nm ofwords
                        ofwords = words x
                        nm = consumelines xs $ Map.insert key val m

loader x = consumelines x Map.empty

sol s = (loader $ liness s) Map.! "a"

splitter :: [a] -> ([a],[a])
splitter = split' ([],[]) True
         where 
           split' (a,b) True (x:xs) = split' (x:a,b) False xs
           split' (a,b) False (x:xs) = split' (a,x:b) True (xs)
           split' (a,b) _ [] = (reverse a,reverse b)

solve :: String -> String
solve x = show $ sol x

main :: IO()
main = do 
    contents <- readFile "input.txt"
    putStrLn $ solve contents
